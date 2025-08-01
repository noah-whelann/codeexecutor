google cloud run url:
https://pythonexecutor-yw5rmvvz6a-uc.a.run.app/execute

local host url:
http://localhost:8080/execute

cURL example:
curl -X POST https://pythonexecutor-yw5rmvvz6a-uc.a.run.app/execute -H "Content-Type: application/json" -d "{\"script\": \"def main():\n    print(\\\"Hello there\\\")\n    return {\\\"status\\\": \\\"success\\\"}\"}"


local docker build: 
docker build -t codeexecutor .

local docker run:
docker run --rm \
  --cap-add SYS_ADMIN \
  -e USE_NSJAIL=true \
  -p 8080:8080 \
  codeexecutor
