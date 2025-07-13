import React  from 'react'; 

const FollowUpQuestions = () => {
  
  return (
    <div>
      
        <div style={{backgroundColor: "Gray", padding:"10px 15px", border: "2px solid brown"}}>
          <p   onClick={() => sendUserMessage(props.question1)}> {props.question1} </p>
     
        </div>
        <div style={{backgroundColor: "Gray", padding:"10px 15px", border: "2px solid brown"}}>
             <p   onClick={() => sendUserMessage(props.question2)}> {props.question2} </p>
        </div>
        <div style={{backgroundColor: "Gray", padding:"10px 15px", border: "2px solid brown"}}>
            <p   onClick={() => sendUserMessage(props.question3)}> {props.question3} </p>
        </div>

        <div style={{backgroundColor: "Gray", padding:"10px 15px", border: "2px solid brown"}}>
           <p   onClick={() => sendUserMessage(props.question4)}> {props.question4} </p>
        </div>
    </div>
  
  );
};

export default FollowUpQuestions;
