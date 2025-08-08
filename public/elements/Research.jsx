import React ,  { useEffect, useState } from 'react';

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

function runTask() {
    let timer =  null

    let url = "http://localhost:8086/stages/"+ props.correlationId
    fetch(url)
    .then((response) => response.json())
    .then((json) => {

        if(json.status === 1)
        {
            alert('calling')
            callAction({name: "action_button", payload: {correlationId:props.correlationId}})
            clearTimeout(timer)
        }
        else
        {
            timer = setTimeout(runTask,5000)
        }
    })
    .catch((error) => {
        alert(error)
    });

}

function click()
{
    alert('called')
    callAction({name: "action_button", payload: {correlationId:props.correlationId}})
}
const Research = () =>
{
    function sourcesClicked()
    {
        setShowSources(true)
        setShowAnswer(false)
    }

    function answerClicked()
    {
        setShowSources(false)
        setShowAnswer(true)
    }

    const [showSources, setShowSources] = useState(true)
    const [showAnswer, setShowAnswer] = useState(true)
   useEffect(() => {
       runTask()
      }, []);

    return  (
          <div className='projectcommands'>

                <button onClick={sourcesClicked}>Sources</button>
                <button onClick={answerClicked}>Answer</button>

            {/*<div id='sources' className={`sources ${showSources ? 'show' : ''}`} ></div>*/}
            {/*<div id='answer' className={`snswer ${showAnswer ? 'show' : ''}`}></div>*/}
        </div>
        )
}

export  default Research