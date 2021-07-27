#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load up .env
set -o allexport
[[ -f "${__dir}/.env" ]] && source "${__dir}/.env"
set +o allexport

echo "Creating VM Instance"
gcloud compute instances create "${VM_NAME}" \
  --zone="${VM_ZONE}" \
  --machine-type="${VM_MACHINE_TYPE}" \
  --min-cpu-platform="Intel Haswell" \
  --image="${VM_IMAGE}" \
  --image-project="${VM_IMAGE_PROJECT}" \
  --boot-disk-size="${VM_BOOT_DISK_SIZE}" \
  --metadata-from-file=startup-script="${__dir}/startup-script.sh"

echo "VM Instance started"
echo "To connect:"
echo "  gcloud compute ssh --zone ${VM_ZONE} ${VM_NAME}"
