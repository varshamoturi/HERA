export PROJECT_ID= herav3
export REGION=us-west1
export CONNECTION_NAME=herav3:us-west1:herapsql

gcloud builds submit --tag gcr.io/herav3/hera  --project $PROJECT_ID

gcloud run deploy poll --image gcr.io/herav3/hera --platform managed --region $REGION --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --project $PROJECT_ID