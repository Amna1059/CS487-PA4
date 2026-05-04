import azure.functions as func
import azure.durable_functions as df
import os, json, time, requests

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="orchestrators/my_orchestrator", methods=["POST"])
@app.durable_client_input(client_name="client")
async def http_starter(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    order = req.get_json()
    instance_id = await client.start_new("my_orchestrator", client_input=order)
    return client.create_check_status_response(req, instance_id)

@app.orchestration_trigger(context_name="context")
def my_orchestrator(context: df.DurableOrchestrationContext):
    order = context.get_input()
    validation_result = yield context.call_activity("validate_activity", order)
    if not validation_result.get("valid"):
        return {"status": "rejected", "reason": validation_result.get("reason", "Unknown")}
    report_url = yield context.call_activity("report_activity", order)
    return {"status": "completed", "report_url": report_url}

@app.activity_trigger(input_name="order")
def validate_activity(order: dict) -> dict:
    validate_url = os.environ["VALIDATE_URL"]
    # VALIDATE_URL is already the full endpoint e.g. http://<IP>:8080/validate
    r = requests.post(validate_url, json=order)
    r.raise_for_status()
    return r.json()

@app.activity_trigger(input_name="order")
def report_activity(order: dict) -> str:
    from azure.mgmt.containerinstance import ContainerInstanceManagementClient
    from azure.mgmt.containerinstance.models import (
        ContainerGroup, Container, ResourceRequirements, ResourceRequests,
        ImageRegistryCredential, EnvironmentVariable, OperatingSystemTypes,
        ContainerGroupRestartPolicy,
    )
    from azure.identity import DefaultAzureCredential

    sub_id   = os.environ["SUBSCRIPTION_ID"]
    rg       = os.environ["REPORT_RG"]
    loc      = os.environ["REPORT_LOCATION"]
    image    = os.environ["REPORT_IMAGE"]
    order_id = order["order_id"]
    name     = f"ci-report-{order_id.lower()}"

    credential = DefaultAzureCredential(managed_identity_client_id=os.environ.get("AZURE_CLIENT_ID"))
    client = ContainerInstanceManagementClient(credential, sub_id)

    group = ContainerGroup(
        location=loc,
        os_type=OperatingSystemTypes.linux,
        restart_policy=ContainerGroupRestartPolicy.never,
        image_registry_credentials=[ImageRegistryCredential(
            server=os.environ["ACR_SERVER"],
            username=os.environ["ACR_USERNAME"],
            password=os.environ["ACR_PASSWORD"])],
        containers=[Container(
            name="report",
            image=image,
            resources=ResourceRequirements(
                requests=ResourceRequests(cpu=1.0, memory_in_gb=1.5)),
            environment_variables=[
                EnvironmentVariable(name="ORDER_ID",    value=order_id),
                EnvironmentVariable(name="ORDER_JSON",  value=json.dumps(order)),
                EnvironmentVariable(name="STORAGE_CONN", secure_value=os.environ["STORAGE_CONN"]),
            ]
        )]
    )

    client.container_groups.begin_create_or_update(rg, name, group).result()

    # Poll until Succeeded or Failed (max 5 minutes)
    for _ in range(60):
        info = client.container_groups.get(rg, name)
        state = info.instance_view.state if info.instance_view else None
        if state in ("Succeeded", "Failed"):
            break
        time.sleep(5)

    # Clean up ACI so it stops billing
    client.container_groups.begin_delete(rg, name)

    # Return blob URL
    account = os.environ["STORAGE_CONN"].split(";AccountName=")[1].split(";")[0]
    return f"https://{account}.blob.core.windows.net/reports/{order_id}.pdf"
