*** Settings ***
Library    PexpectLibrary

*** Tasks ***

Main   
    Serial Spawn    COM11    { 'baudrate': 115200 }
    Send Line    hello
    Send Line    exit
    ${data}    Read Line
    Log To Console    Received: ${data}    
    Close