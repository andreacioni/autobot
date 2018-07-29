#!/bin/bash
# Many thanks to @evilsocket (https://github.com/evilsocket/arc/blob/master/new_release.sh) 
# for this usefull file

echo "Creating new version"

CURRENT_VERSION=$(cat autobot/version/version.py | grep version | awk '{print $3}' | cut -d '"' -f 2)
FILES=(
    setup.py
    autobot/version/version.py
)

echo "Current version is: $CURRENT_VERSION. Enter new version:"

read NEW_VERSION

echo "New version is: $NEW_VERSION"

for FILE in "${FILES[@]}"
do
    echo "Patching file $FILE"
    sed -i "" "s/$CURRENT_VERSION/$NEW_VERSION/g" $FILE
    git add $FILE
done

git commit -m "Releasing v$NEW_VERSION"

git push

git tag -a v$NEW_VERSION -m "Release v$NEW_VERSION"

git push origin v$NEW_VERSION