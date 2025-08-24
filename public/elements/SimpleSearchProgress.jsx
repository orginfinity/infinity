import React ,  { useEffect, useState } from 'react';

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
    const [showSpinner, setShowSpinner] = useState(true)
   useEffect(() => {
        setShowSpinner(props.showSpinner)

       // startuptask()
      }, []);

    return  (
          <div id='simplesearchprogress' className='simplesearchprogress'  >
    
              <img className={`spinner ${showSpinner ? 'show' : ''}`} src="http://localhost:8086/spinner" width="40" height="40" />
                <p className={`spinner ${showSpinner ? 'show' : ''}`} >{props.message}</p>
        </div>
        )
}

export  default Research