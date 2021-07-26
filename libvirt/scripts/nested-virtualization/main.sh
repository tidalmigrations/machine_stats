#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# Load up .env
set -o allexport
[[ -f .env ]] && source .env
set +o allexport

echo "Creating VM Instance"
gcloud compute instances create "${VM_NAME}" \
  --zone="${VM_ZONE}" \
  --machine-type="${VM_MACHINE_TYPE}" \
  --min-cpu-platform="Intel Haswell" \
  --image="${VM_IMAGE}" \
  --image-project="${VM_IMAGE_PROJECT}" \
  --boot-disk-size="${VM_BOOT_DISK_SIZE}" \
  --metadata-from-file=startup-script=startup-script.sh

echo "VM Instance started"
echo "To connect:"
echo "  gcloud compute ssh --zone ${VM_ZONE} ${VM_NAME}"
