SHELL = /usr/bin/env bash -euo pipefail
STACK_NAME := pet-store-api

PIPFILE_MD5_HASH := $(shell md5 -q  Pipfile.lock)

package: guard-S3BUCKET
	@echo "start package"
	$(eval S3_URI :=  s3://${S3BUCKET}/layers/${PIPFILE_MD5_HASH})
	$(eval EXISTS_LAYER :=  $(shell aws s3 ls s3://${S3BUCKET}/layers/${PIPFILE_MD5_HASH} 1>&2 2> /dev/null && echo 'exists' || echo 'non_exists'))
	@if [ "${EXISTS_LAYER}" = "exists" ]; then \
	  echo "Layer for ${PIPFILE_MD5_HASH} allready exists"; \
	else \
          PIP_TARGET="layer/python" pipenv sync && \
	  cd layer; zip -r layer.zip python && \
	  aws s3 cp layer.zip s3://${S3BUCKET}/layers/${PIPFILE_MD5_HASH}; \
	fi
	@sam package --s3-bucket ${S3BUCKET} --template-file template.yaml --output-template-file output.yaml
deploy: package
	@echo "start deploy"
	@sam deploy --template-file output.yaml  --stack-name ${STACK_NAME} --capabilities CAPABILITY_IAM --parameter-overrides \
	    S3BucketForLayerPackage=${S3BUCKET} \
	    S3KeyForLayerPackage=layers/${PIPFILE_MD5_HASH}
guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi
.PHONY: \
	deploy \
	package
