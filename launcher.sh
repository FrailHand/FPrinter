# !/bin/bash

BIN_PATH="/fprinter/bin"
FF_PATH="/fprinter/fprinter/frontend"

${BIN_PATH}/fprinter_backend
sleep 3
sudo ${BIN_PATH}/pserve ${FF_PATH}/development.ini