mkdir User0
start python client.py "User0" "User0/" "localhost" 50000 "localhost" 13370 60000 10
sleep 3
mkdir User1
start python client.py "User1" "User1/" "localhost" 50001 "localhost" 50000 60010 10
sleep 3
mkdir User2
start python client.py "User2" "User2/" "localhost" 50002 "localhost" 50001 60020 10
sleep 3
mkdir User3
start python client.py "User3" "User3/" "localhost" 50003 "localhost" 50002 60030 10
sleep 3
mkdir User4
start python client.py "User4" "User4/" "localhost" 50004 "localhost" 50003 60040 10
sleep 3
mkdir User5
start python client.py "User5" "User5/" "localhost" 50005 "localhost" 50004 60050 10
REM sleep 3
REM mkdir User6
REM start python client.py "User6" "User6/" "localhost" 50006 "localhost" 50005 60060 10
REM sleep 3
REM mkdir User7
REM start python client.py "User7" "User7/" "localhost" 50007 "localhost" 50006 60070 10
REM sleep 3
REM mkdir User8
REM start python client.py "User8" "User8/" "localhost" 50008 "localhost" 50007 60080 10