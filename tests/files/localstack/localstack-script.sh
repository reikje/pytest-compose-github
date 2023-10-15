#!/bin/bash

export AWS_REGION=$REGION
if [ "$REGION" != "us-east-1" ]; then
  awslocal s3api create-bucket --bucket "$BUCKET_NAME_INCOMING" --create-bucket-configuration LocationConstraint="$REGION"
else
  awslocal s3api create-bucket --bucket "$BUCKET_NAME_INCOMING"
fi

awslocal s3 cp /tmp/bank1 s3://$BUCKET_NAME_INCOMING/bank1 --recursive
