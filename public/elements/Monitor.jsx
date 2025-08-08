
import React, { useState, useEffect } from 'react';
//
// window.addEventListener("message", (event) => {
//     if(event.origin === "http://localhost:3000" && event.data.status === "processing")
//     {
//         if(event.data.command === "sendIPTrackedMessage")
//         {
//             let chatinput = document.getElementById('chat-input')
//
//             event.data.status = "done"
//             sendUserMessage(chatinput.innerText)
//             let msg = {command:"updateIPBasedMsgCount",correlationId:"",result:"",status:"processing"}
//             window.parent.postMessage(msg, '*')
//         }
//
//        if(event.data.command === "sendEmailTrackedMessage")
//         {
//             let chatinput = document.getElementById('chat-input')
//             event.data.status = "done"
//             sendUserMessage(chatinput.innerText)
//             let msg = {command:"updateEmailBasedMsgCount",correlationId:"",result:"",status:"processing"}
//             window.parent.postMessage(msg, '*')
//         }
//
//        if(event.origin === "http://localhost:3000" && event.data.command === "setmode") {
//            if (event.data.command === "sendIPTrackedMessage") {
//                event.data.status = "done"
//                let mode = event.data.mode
//                setMode(mode)
//            }
//        }
//
//
//     }
// });

function checkAudioPermission()
{
    let msg = {command:"audioPermissions",correlationId:"",result:"",status:"processing"}
    window.parent.postMessage(msg, '*')
}

function checkResearchPermission()
{
    let msg = {command:"researchPermissions",correlationId:"",result:"",status:"processing"}
    window.parent.postMessage(msg, '*')
}

function sendMessage()
{
   let msg = {command:"msgPermissions",correlationId:"",result:"",status:"processing"}
    window.parent.postMessage(msg, '*')
}

function Monitor()
{
    useEffect(() => {

      }, []);

    window.addEventListener("message", (event) => {
    if(event.origin === "http://localhost:3000" && event.data.status === "processing")
    {
       //  if(event.data.command === "sendIPTrackedMessage")
       //  {
       //      alert('here')
       //      let chatinput = document.getElementById('chat-input')
       //
       //      event.data.status = "done"
       //      sendUserMessage(chatinput.innerText)
       //      let msg = {command:"updateIPBasedMsgCount",correlationId:"",result:"",status:"processing"}
       //      window.parent.postMessage(msg, '*')
       //  }
       //
       // if(event.data.command === "sendEmailTrackedMessage")
       //  {
       //      let chatinput = document.getElementById('chat-input')
       //      event.data.status = "done"
       //      sendUserMessage(chatinput.innerText)
       //      let msg = {command:"updateEmailBasedMsgCount",correlationId:"",result:"",status:"processing"}
       //      window.parent.postMessage(msg, '*')
       //  }

       // if(event.origin === "http://localhost:3000" && event.data.command === "setMode") {
       //      event.data.status = "done"
       //      let modeVal = event.data.mode
       //     document.getElementById('mode').innerText  = modeVal
       //      // setMode(modeVal)
       // }

        if(event.origin === "http://localhost:3000" && event.data.status === "processing") {
            if(event.data.command === "setSearchMode")
            {
                event.data.status = "done"
                alert(event.data.command)
            }
       }

        if(event.origin === "http://localhost:3000" && event.data.status === "processing") {
            if(event.data.command === "setProjectMode")
            {
                event.data.status = "done"
                alert(event.data.command)
            }
       }
    }
});
    function SetupPromptPanel()
    {
        let submit = document.getElementById('chat-submit')
        let parentNode = submit.parentNode
        let chatPanel = parentNode.parentNode
        let defaultaudiobtn = Array.from(parentNode.previousSibling.querySelectorAll('button'))[1];
        // defaultaudiobtn.parentNode.removeChild(defaultaudiobtn)

        defaultaudiobtn.addEventListener("onclick", function() {
            alert("Button clicked!");
        });

        submit.parentElement.removeChild(submit)
        chatPanel.classList.add("promptpanel")

        const audiobtn  = document.createElement('button');
        audiobtn.onclick = (elem) => {checkAudioPermission()}
        audiobtn.classList.add("audiobtn")
        audiobtn.innerHTML = "Audio"

        const researchbtn  = document.createElement('button');
        researchbtn.onclick = (elem) => {checkResearchPermission()}
        researchbtn.innerHTML = "Research"
        researchbtn.classList.add("researchbtn")

        const sendmsgbtn  = document.createElement('button');
        sendmsgbtn.onclick = (elem) => {sendMessage()}
        sendmsgbtn.innerHTML = "Send"
        sendmsgbtn.classList.add("sendmsgbtn")

        parentNode.prepend(audiobtn)
        parentNode.prepend(researchbtn)
        parentNode.prepend(sendmsgbtn)
    }
      useEffect(() => {
        // SetupPromptPanel()

      }, []);

      return (
          <div className="header">
                <p id="mode"></p>
            </div>
      );
}
export default Monitor;
