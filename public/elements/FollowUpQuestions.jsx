import React  from 'react'; 

const FollowUpQuestions = () => {
  
  return (
    <div>
      
        <div style={{ padding:"10px 15px", "border-top": "1px solid gray",  "display": "flex",  "cursor": "pointer"}}>
          <p   onClick={() => sendUserMessage(props.question1)} style={{ "flex": "1" }}> {props.question1} </p>
          <p> {"+"} </p>   
        </div>
        <div style={{ padding:"10px 15px", "border-top": "1px solid gray",  "display": "flex", "cursor": "pointer"}}>
             <p  style={{ "flex": "1" }} onClick={() => sendUserMessage(props.question2)}> {props.question2} </p>
              <p> {"+"} </p>   
        </div>
        <div style={{ padding:"10px 15px", "border-top": "1px solid gray",  "display": "flex", "cursor": "pointer"}}>
            <p  style={{ "flex": "1" }} onClick={() => sendUserMessage(props.question3)}> {props.question3} </p>
             <p> {"+"} </p>   
        </div>

        <div style={{ padding:"10px 15px", "border-bottom": "1px solid gray","border-top": "1px solid gray",  "display": "flex", "cursor": "pointer"}}>
           <p style={{ "flex": "1" }}  onClick={() => sendUserMessage(props.question4)}> {props.question4} </p>
            <p> {"+"} </p>   
        </div>
    </div>
  
  );
};

export default FollowUpQuestions;
