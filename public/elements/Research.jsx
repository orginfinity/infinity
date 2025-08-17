import React ,  { useEffect, useState, memo } from 'react';
// import spinner from './spinner.gif'


function getResearchResults()
{
    let url = "http://localhost:8086/stages/"+ props.correlationId
    fetch(url)
    .then((response) => response.json())
    .then((json) => {
        return json.status
    })
    .catch((error) => {
        return 0
    });
}

let count = 0;

function click()
{
    alert('called')
    callAction({name: "action_button", payload: {correlationId:props.correlationId}})
}
let id = null


const Research = () =>
{
const [statusMsg, setStatusMsg] = useState("")
// const [es, setES] = useState(null)
const eventSource = new EventSource("http://localhost:8088/stream/"+ props.correlationId);

     async function fetchJokes() {

        eventSource.onmessage = (event) => {
            let data = JSON.parse(event.data.toString())
            console.log(data.statusmsg)
            setStatusMsg(data.statusmsg);

            if(data.statusmsg === "Done" || data.statusmsg === "Error" || data.statusmsg === "Timeout")
            {
                // let submit = document.getElementById('chat-submit')
                // submit.disabled = false
                eventSource.close()
            }
        };

        eventSource.onerror = () => {
             // let submit = document.getElementById('chat-submit')
            // submit.disabled = false
            alert("EventSource failed.");
            return () => eventSource.close();
        };
        return () => { eventSource.close();}

    }
   useEffect(() => {
       if(props.correlationId !== "start")
       {
           fetchJokes()
       }
      }, [statusMsg]);

    return  (
          <div id='projectcommands' className='projectcommands'>
                {/*<p  id='dummy'>{props.correlationId}</p>*/}
              <div className={`spinner ${statusMsg !=='Done' && statusMsg !=='Error' &&  statusMsg !=='Timeout'  ? 'show' : ''}`}>
                  <img    src="http://localhost:8086/spinner" width="40" height="40" />
                    {/*<p className={`statusmsg ${statusMsg !=='Done'   ? 'show' : ''}`}>{statusMsg}</p>*/}
              </div>
              <p>{statusMsg}</p>

        </div>
        )
}

export  default Research