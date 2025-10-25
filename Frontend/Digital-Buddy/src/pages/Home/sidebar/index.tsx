import { FileText, Lightbulb} from "lucide-react"

export default function SidebarHome(){
    return (
        <>
        <div className="grid grid-rows-6 h-screen">
            <div>

            </div>

            <div className="text-white p-4">
                   <button className="hover:bg-blue-600 hover:rounded-2xl hover:p-1 hover:px-3" >
                     <div className="flex ">
                          <FileText className="h-5 w-5 mr-2"/>
                          <label className="ml-2">Mood Logs</label>
                     </div>
                   </button>
                   <button className="hover:bg-blue-600 hover:rounded-2xl hover:p-1 hover:px-3" >
                     <div className="flex ">
                          <Lightbulb className="h-5 w-5 mr-2"/>
                          <label className="ml-2">Suggestions</label>
                     </div>
                   </button>     
    
            </div>
        </div>
        </>
    )

}