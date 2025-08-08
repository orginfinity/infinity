import React , { useEffect, useRef } from 'react';

const ResearchSteps = () =>
{
    let allfaviconsources = []
    for(let i = 0; i< props.promptactioncount ; i++)
    {
        let counts = props["favicon" + i.toString()].length
        let sources = props["sources" + i.toString()]
        let favicons = props["favicon" + i.toString()]

        let faviconsources = []
        for(let j = 0; j< counts ; j++)
        {
            let temp = [sources[j],favicons[j]]
            faviconsources[j] = temp
        }

        allfaviconsources[i] = faviconsources
    }

    const SourceLink = ({ data }) => {
        let textContent = data[0].slice(0,75) + "..."
        return (
            <div className="projectLink">
                <img className='img_favicons' src = {data[1]}></img>
                <a className='uri' target='_blank' href={data[0]}>  {textContent} </a>
            </div>
      );
    };
    return (
        <div id='projectdiv' className='projectsources'>

            {Array.from({ length: allfaviconsources.length }).map((_, index) => (

                <div className="stagedetail" >
                    <p className='stepidentifier'>{index}</p>
                    <p className='projectaction'>{props["action"+index.toString()]}</p>
                    <br/>
                        {Object.values(allfaviconsources[index]).map(value => (
                              <SourceLink data={[value[0],value[1]]} />
                        ))}

                </div>
            ))}
         </div>
    )
}

export  default  ResearchSteps
//
//
//
//
// const sourcesClicked = (elem) =>
//     {
//         parentElem =  elem.target
//
//         while (parentElem != null)
//         {
//             parentElem = parentElem.parentNode
//             if (parentElem != null )
//             {
//                 if(parentElem.hasAttribute('data-step-type') )
//                 {
//
//                     answerWindow = parentElem.nextSibling
//                     if(answerWindow == null)
//                     {
//                         return
//                     }
//                     answerWindow = answerWindow.getElementsByClassName('message-content')[0]
//
//                     child =Array.from(answerWindow.children)[0]
//
//                     if(child != null)
//                     {
//                         child.style.display = "none"
//                     }
//                     sourcestable = answerWindow.querySelector('#sourcesTable');
//
//                     if(sourcestable == null)
//                     {
//                         answerWindow.appendChild(loadSources())
//                     }
//                     else
//                     {
//                         sourcestable.style.display = "inline"
//                     }
//                     break
//                 }
//
//             }
//
//             parentElem = parentElem.parentNode
//         }
//     }
//
// const answerClicked = (elem) =>
//     {
//         parentElem =  elem.target
//
//         while (parentElem != null)
//         {
//             parentElem = parentElem.parentNode
//             if (parentElem != null )
//             {
//                 if(parentElem.hasAttribute('data-step-type') )
//                 {
//
//                     answerWindow = parentElem.nextSibling
//                     answerWindow = answerWindow.getElementsByClassName('message-content')[0]
//
//                     child =Array.from(answerWindow.children)[0]
//                     child.innerHtml = props.answer
//
//                     if(child != null)
//                     {
//                         child.style.display = "inline"
//                     }
//
//                     sourcestable = answerWindow.querySelector('#sourcesTable')
//
//                     if (sourcestable != null)
//                     {
//                         sourcestable.style.display= "none"
//                     }
//
//                     break
//                 }
//
//             }
//             parentElem = parentElem.parentNode
//         }
//     }
//
// const enableButtons = () =>
// {
//    btnSources = document.getElementById('sources')
//
//    if(props.sourceCount > 0){
//     btnSources.style.display = "inline"
//    }
//
//    btnAnswer = document.getElementById('answer')
//    if(props.answerCount > 0){
//     btnAnswer.style.display = "inline"
//    }
// }
//
// const ResearchSteps = () =>
// {
//     const buttonRef = useRef(null);
//     useEffect(() => {
//
//         if (buttonRef.current) {
//             buttonRef.current.click()
//         }
//         enableButtons()
//       }, []);
//
//     return (
//         <div id="headerelem">
//
//             <table  >
//                 <tr>
//                     <td>
//                         <button className="headerbutton  bg-accent"  ref={buttonRef} onClick={sourcesClicked}  style={{display:"inline"}} id="sources"  >SOURCES</button>
//                     </td>
//                     <td>
//                         <button className="headerbutton  bg-accent" onClick={answerClicked}  id="answer"  >ANSWER</button>
//                     </td>
//
//                 </tr>
//             </table>
//         </div>
//     )
// }
//
// const loadSourceLinks = () =>
// {
// }
//
// const loadSources = () =>
// {
//     researchstepsparent = document.getElementById('sources')
//     const sourcesTable =   document.createElement('table')
//     sourcesTable.id = "sourcesTable"
//
//
//      for (let i = 0; i < props.promptactioncount; i++)
//      {
//         newRow = sourcesTable.insertRow();
//
//         let prompt = props["prompt"+ i.toString()]
//         let action = props["action"+i.toString()]
//
//
//         const cell1 = newRow.insertCell(0);
//         cell1.classList.add('tdforresearchsteps')
//         const promptElement = document.createElement('p');
//         promptElement.classList.add('researchstepprompt')
//
//         promptElement.innerHTML = prompt
//         cell1.appendChild(promptElement)
//
//         newRow = sourcesTable.insertRow();
//         const cell2 = newRow.insertCell(0);
//
//         const actionElement = document.createElement('p');
//         actionElement.innerHTML = action
//          cell2.classList.add("fulltd")
//         cell2.appendChild(actionElement)
//
//         let sources = props["sources"+i.toString()]
//         let favicons = props["favicon"+i.toString()]
//          sources = sources.replace(/'/g,"\"")
//          favicons = favicons.replace(/'/g,"\"")
//
//          websiteLinks = JSON.parse(sources)
//          faviconLinks = JSON.parse(favicons)
//
//        for (let j = 0; j < websiteLinks.length; j++)
//        {
//             newRow2 = sourcesTable.insertRow()
//             const cell3 = newRow2.insertCell(0);
//
//             const divelem = document.createElement('div')
//
//             divelem.classList.add('.panel-header')
//             const imgElement = document.createElement('img');
//             // imgElement.classList.add("img_favicons")
//             imgElement.src = faviconLinks[j];
//             divelem.appendChild(imgElement)
//             // cell3.classList.add('smalltd')
//
//            const websiteElement = document.createElement('p');
//             websiteElement.innerHTML = websiteLinks[j]
//            divelem.appendChild(websiteElement)
//             cell3.appendChild(divelem)
//
//         }
//      }
//
//     return sourcesTable
// }
//
// export default ResearchSteps