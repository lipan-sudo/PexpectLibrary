*** Settings ***
Library    PexpectLibrary

*** Tasks ***

Main   
    Serial Spawn    COM10    { 'baudrate': 115200 }
    Expect Exact    exit    
    ${before}    Before
    Log To Console    Received: ${before}
    Send Line    message from server
    Close