@Echo off

set "inkscapePath=C:\Program Files\Inkscape\inkscape.exe"
set /a count=0
set validInput1=svg
set validInput2=pdf
set validInput3=eps
set validOutput1=eps
set validOutput2=pdf
set validOutput3=png

echo This script allows you to convert all files in this folder from one file type to another.

set valid=0
echo Allowed file types for source: %validInput1%, %validInput2%, %validInput3%

:whileInNotCorrect
	set /p sourceType=What file type do you want to use as a source?
	if "%sourceType%" EQU "%validInput1%" set valid=1
	if "%sourceType%" EQU "%validInput2%" set valid=1
	if "%sourceType%" EQU "%validInput3%" set valid=1
	if %valid% EQU 0 (
		echo Invalid input! Please use one of the following: %validInput1%, %validInput2%, %validInput3%
		goto :whileInNotCorrect
	)

set valid=0
echo Allowed file types for output: %validOutput1%, %validOutput2%, %validOutput3%      
:whileOutNotCorrect
	set /p outputType=What file type do you want to convert to?
	if "%outputType%" EQU "%validOutput1%" set valid=1
	if "%outputType%" EQU "%validOutput2%" set valid=1
	if "%outputType%" EQU "%validOutput3%" set valid=1
	if %valid% EQU 0 (
		echo Invalid input! Please use one of the following: %validOutput1%, %validOutput2%, %validOutput3%   
		goto :whileOutNotCorrect
	)

:: Set DPI for exported file
set /p dpi=With what dpi should it be exported (e.g. 300)?

:: Running through all files found with the defined ending
for %%i in (.\*.%sourceType%) do (
	set /a count=count+1
	echo %%i to %%~ni.%outputType%
	"%inkscapePath%" --without-gui --file="%%i" --export-%outputType%="%%~ni.%outputType%" --export-dpi=%dpi% --export-text-to-path
)
   
echo %count% file(s) converted from %sourceType% to %outputType%!
   
pause