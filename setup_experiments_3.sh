#!/bin/bash
rm -rf subjects
mkdir subjects

git clone git://github.com/FlyingPumba/Equate.git subjects/com.llamacorp.equate
git clone git://github.com/FlyingPumba/home-assistant-Android.git subjects/io.homeassistant.android
git clone git://github.com/FlyingPumba/kolabnotes-android.git subjects/org.kore.kolabnotes.android
git clone git://github.com/FlyingPumba/androidclient.git subjects/org.kontalk
git clone git://github.com/FlyingPumba/MicroPinner.git subjects/de.dotwee.micropinner
git clone git://github.com/FlyingPumba/MyExpenses.git subjects/org.totschnig.myexpenses
git clone git://github.com/FlyingPumba/ocreader.git subjects/email.schaal.ocreader
git clone git://github.com/FlyingPumba/shoppinglist.git subjects/org.openintents.shopping
git clone git://github.com/FlyingPumba/Omni-Notes.git subjects/it.feio.android.omninotes.foss
git clone git://github.com/FlyingPumba/onetimepad.git subjects/com.onest8.onetimepad
git clone git://github.com/FlyingPumba/orgzly-android.git subjects/com.orgzly
git clone git://github.com/FlyingPumba/poet-assistant.git subjects/ca.rmen.android.poetassistant

# update subject's etg.config file
find subjects/ -name etg.config -exec sed -i "s|/home/ivan/src|$(pwd)|g" {} \;
find subjects/ -name etg.config -exec sed -i "s|/home/ivan/latex/etg-paper/experiments|$(pwd)|g" {} \;

# delete any existing ETG-generated tests
find . -name "ETGTestCase*" -delete

rm -rf etg
git clone https://github.com/FlyingPumba/etg.git

rm -rf etg-mate
git clone https://github.com/FlyingPumba/etg-mate.git

rm -rf etg-mate-server
git clone https://github.com/FlyingPumba/etg-mate-server.git

virtualenv -p python3 .env
source .env/bin/activate
pip install -r requirements.txt
