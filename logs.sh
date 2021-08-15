API=$1
open $(cortex logs $API --env factorio | grep https)