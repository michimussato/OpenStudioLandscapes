#!/usr/bin/env bash


mkdir -p /git

git -C /git clone https://github.com/likec4/likec4.git
git -C /git clone https://github.com/asdf-vm/asdf.git --branch v0.15.0

source /git/asdf/asdf.sh

cd /git/likec4 || exit 1
asdf plugin add nodejs
asdf plugin add yarn
asdf plugin add dprint
asdf install
yarn install
yarn build

exit 0
