#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load up .env
set -o allexport
[[ -f "${__dir}/.env" ]] && source "${__dir}/.env"
set +o allexport

vm_status() {
  gcloud compute instances list \
    --filter="name='${VM_NAME}'" \
    --zones="${VM_ZONE}" \
    --format="value(status)"
}

create_vm() {
  echo "Creating VM Instance '${VM_NAME}'..." >&2

  gcloud compute instances create "${VM_NAME}" \
    --zone="${VM_ZONE}" \
    --machine-type="${VM_MACHINE_TYPE}" \
    --min-cpu-platform="Intel Haswell" \
    --image="${VM_IMAGE}" \
    --image-project="${VM_IMAGE_PROJECT}" \
    --boot-disk-size="${VM_BOOT_DISK_SIZE}" \
    --metadata-from-file=startup-script="${__dir}/startup-script.sh"

  echo "VM Instance '${VM_NAME}' started." >&2
  echo "Give it a few minutes to finish provisioning." >&2
  echo "Check the VM console logs for statup script execution complete." >&2

  print_connection_cmd
}

start_vm() {
  echo "Starting VM Instance '${VM_NAME}'..." >&2
  gcloud compute instances start "${VM_NAME}" \
  --zone="${VM_ZONE}"

  print_connection_cmd
}

print_connection_cmd() {
  echo "To connect:" >&2
  echo "  gcloud compute ssh --project=${CLOUDSDK_CORE_PROJECT} --zone ${VM_ZONE} ${VM_NAME}" >&2
}

main() {
  local status
  status=$(vm_status)
  case $status in
    "RUNNING" )
    echo "VM Instance '${VM_NAME}' is already running." >&2
    print_connection_cmd
    ;;
    "TERMINATED" )
    echo "VM Instance '${VM_NAME}' is stopped." >&2
    start_vm
    ;;
    "" )
    create_vm
    ;;
    * )
    echo "Unknown VM Instance status (${status}) for instance '${VM_NAME}'"
  esac
}

main