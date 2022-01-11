#!/usr/bin/env bash

VERSION=$1

IN_DIR=data/public/$VERSION
OUT_DIR=data/temp/${VERSION}_for_zenodo

echo "OUT: " $OUT_DIR

mkdir $OUT_DIR
cp $IN_DIR/* $OUT_DIR/
pushd $OUT_DIR
zip ndc_$VERSION.zip *.json
rm *.json
popd

cp data/processed/totals_ndc_${VERSION}_*.json $OUT_DIR/