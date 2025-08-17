import React , { useEffect } from 'react'; 
 

const sourcesClicked = (elem) => 
    {   
        parentElem =  elem.target
         
        while (parentElem != null)
        {
            parentElem = parentElem.parentNode
            if (parentElem != null ) 
            {
                if(parentElem.hasAttribute('data-step-type') )
                {  
                    answerWindow = parentElem.nextSibling
                    if(answerWindow == null)
                    {
                        return
                    }

                    answerWindow = answerWindow.getElementsByClassName('message-content')[0]

                    child =Array.from(answerWindow.children)[0]

                    if(child != null)
                    {
                        child.style.display = "none" 
                    }

                    imagesTable = answerWindow.querySelector('#imagesTable');
                    if(imagesTable != null)
                    {
                        imagesTable.style.display = "none"
                    }

                    sourcestable = answerWindow.querySelector('#sourcesTable');
                    if(sourcestable == null)
                    {
                        answerWindow.appendChild(loadSources())                    
                    }
                    else
                    {
                        sourcestable.style.display = "inline"
                    }
                    break
                }
                
            } 
            parentElem = parentElem.parentNode
        }    
    }

const imagesClicked = (elem) => 
    {
        parentElem =  elem.target
         
        while (parentElem != null)
        {

            parentElem = parentElem.parentNode
            if (parentElem != null ) 
            {
                if(parentElem.hasAttribute('data-step-type') )
                {  
                    answerWindow = parentElem.nextSibling
                    answerWindow = answerWindow.getElementsByClassName('message-content')[0]

                    child =Array.from(answerWindow.children)[0]

                    if(child != null)
                    {
                        child.style.display = "none" 
                    }

                    sourcesstable = answerWindow.querySelector('#sourcesTable');
                    if(sourcesstable != null)
                    {
                        sourcesstable.style.display = "none"
                    }
          
                    imagestable = answerWindow.querySelector('#imagesTable');
                    if(imagestable == null)
                    {
                        answerWindow.appendChild(loadImages())                    
                    }
                    else
                    {
                        imagestable.style.display = "inline"
                    }
                     
                    break
                }
                
            } 
            parentElem = parentElem.parentNode
        }
    }

    
const answerClicked = (elem) => 
    {      
        parentElem =  elem.target
    
        while (parentElem != null)
        {

            parentElem = parentElem.parentNode
            if (parentElem != null ) 
            {
                if(parentElem.hasAttribute('data-step-type') )
                {  
                    answerWindow = parentElem.nextSibling
                    answerWindow = answerWindow.getElementsByClassName('message-content')[0]

                    child =Array.from(answerWindow.children)[0]
                    child.innerHtml = props.answer

                    if(child != null)
                    {
                        child.style.display = "inline" 
                    }

                    imagestable = answerWindow.querySelector('#imagesTable')
                    if (imagestable != null)
                    {
                        imagestable.style.display= "none"
                    }

                    sourcestable = answerWindow.querySelector('#sourcesTable')
                    if (sourcestable != null)
                    {
                        sourcestable.style.display= "none"
                    }

                    break
                }
                
            } 
            parentElem = parentElem.parentNode
        }
    }

const enableButtons = () =>
{
   btnSources = document.getElementById('sources')
 
   if(props.sourceCount > 0){
    btnSources.style.display = "inline"
   }
 
   btnImages = document.getElementById('images')
   if(props.imagesCount > 0){
    btnImages.style.display = "inline"
   }
}

const Header = () =>
{    
    useEffect(() => { 
        enableButtons()
      }, []); 
     
    return (
        <div id="headerelem">
             
            <table  > 
                <tr>
                    <td>
                        <button  className="headerbutton  bg-accent" onClick={answerClicked}  id="answer" style={{display:"inline"}}  >ANSWER</button>
                    </td>
                    <td>
                         <button className="headerbutton  bg-accent"  onClick={sourcesClicked}  id="sources"  >SOURCES</button>
                    </td>
                    <td>
                        <button className="headerbutton  bg-accent" onClick={imagesClicked}   id="images"  >IMAGES</button>
                    
                    </td>
                </tr>
            </table> 
        </div>
    )
}

const loadSources = () =>
{     
    const sourcestable =   document.createElement('table')
    sourcestable.id = "sourcesTable" 
     for (let i = 0; i < props.sourceCount; i++)
     { 
        newRow = sourcestable.insertRow();

        let favIconLink = props["favicon"+ i.toString()]
        let thumbnailLink = props["thumbnail"+i.toString()] 
        let websiteLink = props["website"+i.toString()] 
        let contentsLink = props["contents"+i.toString()] 
        let titleText = props["titles"+i.toString()]  
       
        const cell3 = newRow.insertCell(0); 
        const thumbnailElement = document.createElement('img');
        thumbnailElement.classList.add("img_thumbnails") 
        thumbnailElement.src = thumbnailLink;
        cell3.classList.add('mediumtd')
        cell3.appendChild(thumbnailElement) 
        
        const cell2 = newRow.insertCell(0);  
        const websitesElement  = document.createElement('a');   
        websitesElement.target = "_blank"
        websitesElement.style.color = "red"     
        websitesElement.href = websiteLink
        websitesElement.textContent = websiteLink.slice(0, 50) + "...";

        titleElement = newRow.insertCell(0)
        titleElement.innerHTML = titleText
        titleElement.classList.add('sourceTitle')
            
        const contentElement  = document.createElement('p');
        contentElement.innerHTML = contentsLink
        contentElement.classList.add('sourceContent')
        cell2.classList.add('bigtd')
       
        cell2.appendChild(titleElement) 
        cell2.appendChild(contentElement) 
        cell2.appendChild(websitesElement)

        const cell1 = newRow.insertCell(0); 
        const imgElement = document.createElement('img'); 
        imgElement.classList.add("img_favicons")
        imgElement.src = favIconLink;  
        cell1.classList.add('smalltd')
        cell1.appendChild(imgElement)
 
     }
     
     return sourcestable  
}


const loadImages = () =>
{    
    const imagestable =   document.createElement('table')
    imagestable.id = "imagesTable"
    newRow = imagestable.insertRow(); 
     
     for (let i = 0; i < props.imagesCount; i++)
     {  
        if(i%2 == 0)
        {
            newRow = imagestable.insertRow(); 
        }
        let thumbnailLink = props["thumbnailLink"+ i.toString()]
        let displayLink = props["displayLink"+i.toString()] 
        let contextLink = props["contextLink"+i.toString()] 

        const cell1 = newRow.insertCell(0); 
        const imgElement = document.createElement('img');
       imgElement.classList.add('img_thumbnails_big')

        imgElement.src = thumbnailLink;  
        const ahrefElement  = document.createElement('a');
        ahrefElement.target = "_blank"
        ahrefElement.style.color = "red"

        ahrefElement.textContent  = displayLink
        ahrefElement.href = contextLink 
        cell1.classList.add('bigtd')
 
        imgElement.onload = function() {
        if (imgElement.width > 0 && imgElement.height > 0) {
 
            cell1.appendChild(imgElement)
            if (imgElement.complete) { 
                cell1.appendChild(ahrefElement) 
            } 
            else {
                imgElement.addEventListener('load', () => { 
                cell1.appendChild(ahrefElement) 
            });}
        }  
        };

        // cell1.appendChild(imgElement)

        //  if (imgElement.complete) { 
        //         cell1.appendChild(ahrefElement)
        // } 
        // else {
        //     imgElement.addEventListener('load', () => { 
        //     cell1.appendChild(ahrefElement)
        // });}
 
     }
     return imagestable  
}


export default Header