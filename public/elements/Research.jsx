import React , { useEffect } from 'react';

const getResearchResults = (correlationId)  =>
{
    callAction({name: "action_button", payload: {correlationId:correlationId}})
}

function runTask() {
  console.log('Task running every 5 seconds!');
  getResearchResults(props.correlationId)
  // Schedule the next execution
  setTimeout(runTask, 3000); // 3000 milliseconds = 5 seconds
}


const Research = () =>
{
   useEffect(() => {
        runTask()
      }, []);

    return  (
        <div  >
            <p> I AM A CUSTOM MESSAGE: {props.correlationId}</p>
        </div>
        )

}

export  default Research