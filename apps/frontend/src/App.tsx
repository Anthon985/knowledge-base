import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Sidebar } from "@/components/Sidebar"
import { DashboardPage } from "@/components/DashboardPage"
import { UploadPage } from "@/components/UploadPage"
import { SearchPage } from "@/components/SearchPage"
import { ChatPage } from "@/components/ChatPage"
import { DocumentsPage } from "@/components/DocumentsPage"

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        <Sidebar />
        <main className="pl-64">
          <div className="p-8">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App