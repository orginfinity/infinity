import React, {useEffect, useRef, useState} from 'react';
// import ReactMarkdown from 'react-markdown';
// import {jsPDF} from "jspdf"


const Project = () =>
{
      const options = {
        margin: [10, 10, 10, 10],
        filename: 'example.pdf',
        image: { type: 'jpeg', quality: 1 },
        html2canvas: {
        dpi: 300,
        scale: 4,
        letterRendering: true,
        useCORS: true
        },

    };

    const [showSources, setShowSources] = useState(true)
    const [downloadoptions, setDownloadOptions] = useState(false)
    const [showSpinner, setShowSpinner] = useState(true)

    useEffect(() => {
        if(props.mainprompt === "Done")
        {
            setDownloadOptions(true)
        }
        setShowSpinner(props["showSpinner"])
      }, []);

    let allfaviconsources = [] ;

    let pdfContent = "<H1 class=\"pdfsources\"> Sources </H1> <br>"

    for(let i = 0; i< props.promptactioncount ; i++)
    {
        pdfContent +=  "<p class=\"stepidentifier\" >" + (i+1).toString() + "</p>" +  " <br>"
        pdfContent += props["action" + i.toString()] + "<br><br>"
        let counts = props["favicon" + i.toString()].length
        let sources = props["sources" + i.toString()]
        let favicons = props["favicon" + i.toString()]

        let faviconsources = []
        for(let j = 0; j< counts ; j++)
        {
            pdfContent +=  "<a href=\"" + sources[j] + "\" target=\"_blank\" class=\"uri\" /> " + sources[j] + "</a> <br>"
            let temp = [sources[j],favicons[j]]
            faviconsources[j] = temp
        }
        allfaviconsources[i] = faviconsources
    }

    const SourceLink = ({ data }) => {
        let textContent = data[0].slice(0,50) + "..."
        return (
            <div className="projectLink">
                <img className='img_favicons' src = {data[1]}></img>
                <a className='uri' target='_blank' href={data[0]}>  {textContent} </a>
            </div>
      );
    };
    function handlepdfdownload(elem)
    {
        // alert(props["mainprompt"])
        let nextsibling = elem.target.closest('[data-step-type="assistant_message"]').nextSibling;
        pdfContent += "<br> <p class = \"pdfcontent\" > " +  nextsibling.innerHTML + "</p>"
        let pdfelement = document.createElement('div');
        pdfelement.innerHTML = pdfContent
        // alert(pdfContent)
        html2pdf().set(options).from(pdfelement).save(props["mainprompt"]);

    }

    function handledocxownload()
    {
        alert("docx downloading")
    }

    function handlemarkdowndownload()
    {
         const html = '<h1>Hello World</h1><p>This is a paragraph.</p>';
         let markdown = props.answer
        let filename = props.mainprompt
         const blob = new Blob([markdown], { type: 'text/plain' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename + ".md";
        link.click();
        URL.revokeObjectURL(link.href); // Clean up memory
    }
    const DownloadOptions = () =>
    {
        return(
            <div id="downloadoptions" className={`downloadoptions ${downloadoptions ? 'show' : ''}`}>
                <p className='downloadoption' onClick={handlepdfdownload}>PDF</p>
                <p className='downloadoption' onClick={handledocxownload}>Docx</p>
                <p className='downloadoption' onClick={handlemarkdowndownload}>Markdown</p>
            </div>
        )
    }
     function handledownload(elem)
    {
        alert('here')
        setDownloadOptions(true)
     }


    return (
        <div id="projectoutput" >
            {/*<div className='export'>*/}

            {/*    <p onClick={handlepdfdownload} className='download' > Pdf </p>*/}
            {/*    <p onClick={handledocxownload} className='download' > Docx </p>*/}
            {/*    <p onClick={handlemarkdowndownload} className='download' > Markdown </p>*/}

            {/*</div>*/}
            <div id='projectsources' className={`projectsources ${showSources ? 'show' : ''}`}>

                {Array.from({ length: allfaviconsources.length }).map((_, index) => (

                    <div className="stagedetail" >
                        <p className='stepidentifier'>{index+1}</p>
                        <p className='projectaction'>{props["action"+index.toString()]}</p>
                        <br/>
                            {Object.values(allfaviconsources[index]).map(value => (
                                  <SourceLink data={[value[0],value[1]]} />
                            ))}
                    </div>
                ))}
             </div>
        </div>
    )
}

export  default  Project