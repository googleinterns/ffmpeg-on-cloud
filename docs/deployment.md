# Deployment

1. Create a Google Cloud Project if you do not have one. Enable the Cloud Build and Container Registry APIs.

2. Open the [Cloud Shell](https://console.cloud.google.com/home/dashboard?cloudshell=true) in the Cloud Console. All the commands in the following instructions should be run in the Cloud Shell. Alternatively, you can [install the Google Cloud SDK](https://cloud.google.com/sdk/docs) and run the commands in your local terminal.

3. Set the project and compute zone. Replace `$COMPUTE_ZONE` and `$PROJECT_ID` with the [compute zone](https://cloud.google.com/compute/docs/regions-zones#available) and the project ID respectively.

```sh
gcloud config set project $PROJECT_ID
gcloud config set compute/zone $COMPUTE_ZONE
```

4. Create a GKE cluster with [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) enabled. Replace `$CLUSTER_NAME` and `$PROJECT_ID` with the name of the new cluster and the project ID respectively.

```sh
gcloud beta container clusters create $CLUSTER_NAME \
    --release-channel regular \
    --workload-pool=$PROJECT_ID.svc.id.goog
gcloud container clusters get-credentials $CLUSTER_NAME
``` 

You can also [enable Workload Identity on an existing cluster](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#enable_on_existing_cluster).

5. Set up credentials for `gcsfuse`.
   1. Create a service account `gcsfuse` with the Storage Object Creator and Storage Object Viewer roles. Replace `$PROJECT_ID` with the project ID.

   ```sh
   gcloud iam service-accounts create gcsfuse
   gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member=serviceAccount:gcsfuse@$PROJECT_ID.iam.gserviceaccount.com --role=roles/storage.objectCreator
   gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member=serviceAccount:gcsfuse@$PROJECT_ID.iam.gserviceaccount.com --role=roles/storage.objectViewer
   ```

   2. Add policy binding to Kubernetes service account. Replace `$PROJECT_ID` with the project ID.

   ```sh
   kubectl create serviceaccount --namespace default gcsfuse
   gcloud iam service-accounts add-iam-policy-binding \
     --role roles/iam.workloadIdentityUser \
     --member "serviceAccount:$PROJECT_ID.svc.id.goog[default/gcsfuse]" \
     gcsfuse@$PROJECT_ID.iam.gserviceaccount.com
   kubectl annotate serviceaccount \
     --namespace default \
     gcsfuse \
     iam.gke.io/gcp-service-account=gcsfuse@$PROJECT_ID.iam.gserviceaccount.com
   ```

6. Set up credentials for Cloud Endpoints.
   1. Create a service account `endpoints` with the Service Controller and Cloud Trace Agent roles. Replace `$PROJECT_ID` with the project ID.

   ```sh
   gcloud iam service-accounts create endpoints
   gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member=serviceAccount:endpoints@$PROJECT_ID.iam.gserviceaccount.com --role=roles/servicemanagement.serviceController
   gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member=serviceAccount:endpoints@$PROJECT_ID.iam.gserviceaccount.com --role=roles/cloudtrace.agent
   ```

   2. Create a service account key file for the `endpoints` service account. Replace `$PROJECT_ID` with the project ID.
   
   ```sh
   gcloud iam service-accounts keys create service-account-creds.json \
     --iam-account endpoints@$PROJECT_ID.iam.gserviceaccount.com
   ```

   3. Create a Kubernetes secret from the service account key file.

   ```sh
   kubectl create secret generic service-account-creds \
     --from-file=service-account-creds.json
   ```

7. Clone this repository.

```sh
git clone https://github.com/googleinterns/ffmpeg-on-cloud
cd ffmpeg-on-cloud
```

8. Deploy the Cloud Endpoints Service.

```sh
gcloud endpoints services deploy worker/api_descriptor.pb worker/api_config.yaml
```

9. [Enable required services for Cloud Endpoints](https://cloud.google.com/endpoints/docs/quickstart-endpoints#enabling_required_services)

10. Build the containers needed with Cloud Build. Replace `$PROJECT_ID` with the project ID.

```sh
gcloud builds submit worker --tag=gcr.io/$PROJECT_ID/ffmpeg-worker
gcloud builds submit worker --tag=gcr.io/$PROJECT_ID/gcsfuse
```

11. Inside `gcsfuse-daemonset/gcsfuse-daemonset.yaml`, replace `$SERVICE_ACCOUNT` with `gcsfuse`, `$GCLOUD_PROJECT` with the project ID, `$BUCKET_NAME` with the GCS bucket you want to mount. Inside `worker/ffmpeg-worker-deployment.yaml`, replace `$GCLOUD_PROJECT` with the project ID.

12. Deploy Kubernetes objects.

```sh
kubectl apply -k .
```
