@ECHO OFF

for /l %%y in (1, 1, 12) do (

for /l %%x in (1, 1, 11) do (
   echo ##################################################### 
   echo %%y %%x
   echo #####################################################
   python Main.py XGB 
   timeout 30 > NUL
)

)

pause