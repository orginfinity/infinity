
import { Button } from "@/components/ui/button"
import { X, Plus } from 'lucide-react';

export default function News() {
    return (
        <div id="news" className="articles1">
             {Array.from({ length: props.count }).map((_, index) => (
                <div className="articles2" >
                    

                    <img className="newsimage" src={props.urlsToImage[index]} ></img>
                    <div className="articles1">
                        <p> {props.titles[index]} </p>
                        <p>{props.descriptions[index]}</p>
                        <p className="publishdate">Publish Date : {props.publishedOn[index]}</p>
                        <a href = {props.urls[0]} target="_blank" className="newslink"  >{props.urls[0]}</a>
                    </div>
                    
                    <br></br>
                </div>            
                ))}            
        </div>
    );
}