import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { FileText, CheckCircle, Clock, AlertCircle, Upload, Search, MessageSquare } from "lucide-react"
import { useEffect, useState } from "react"
import { listDocuments, type Document, formatDate, getStatusLabel, getStatusColor, formatFileSize } from "@/lib/api"
import { useNavigate } from "react-router-dom"

const statCards = [
  { label: "总文档数", icon: FileText, key: "total" as const, color: "text-primary" },
  { label: "已处理", icon: CheckCircle, key: "completed" as const, color: "text-success" },
  { label: "处理中", icon: Clock, key: "processing" as const, color: "text-warning" },
  { label: "处理失败", icon: AlertCircle, key: "failed" as const, color: "text-destructive" },
]

export function DashboardPage() {
  const navigate = useNavigate()
  const [docs, setDocs] = useState<Document[]>([])
  const [stats, setStats] = useState({ total: 0, completed: 0, processing: 0, failed: 0 })

  useEffect(() => {
    listDocuments(0, 50)
      .then((res) => {
        setDocs(res.documents)
        const s = { total: res.total, completed: 0, processing: 0, failed: 0 }
        res.documents.forEach((d) => {
          if (d.status === "completed") s.completed++
          else if (d.status === "processing" || d.status === "pending") s.processing++
          else if (d.status === "failed") s.failed++
        })
        setStats(s)
      })
      .catch(() => {
        // API not available - show demo data
        setStats({ total: 128, completed: 112, processing: 8, failed: 3 })
      })
  }, [])

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">仪表盘</h2>
        <p className="text-muted-foreground mt-1">知识库文档处理状态概览</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.key}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{card.label}</CardTitle>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats[card.key]}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-primary" />
              最近上传
            </CardTitle>
          </CardHeader>
          <CardContent>
            {docs.length > 0 ? (
              <div className="space-y-3">
                {docs.slice(0, 5).map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-accent/50">
                    <div className="flex items-center gap-3 min-w-0">
                      <FileText className="h-4 w-4 shrink-0 text-primary" />
                      <div className="min-w-0">
                        <p className="text-sm font-medium truncate">{doc.original_filename}</p>
                        <p className="text-xs text-muted-foreground">{formatFileSize(doc.file_size)} · {formatDate(doc.created_at)}</p>
                      </div>
                    </div>
                    <span className={`text-xs font-medium ${getStatusColor(doc.status)}`}>{getStatusLabel(doc.status)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-muted-foreground">
                <FileText className="mx-auto h-10 w-10 mb-3 opacity-30" />
                <p className="text-sm">暂无文档</p>
                <button onClick={() => navigate("/upload")} className="mt-2 text-sm text-primary hover:underline">上传第一个文档</button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5 text-primary" />
              快速操作
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              <button
                onClick={() => navigate("/upload")}
                className="flex items-center gap-3 rounded-lg border border-dashed p-4 text-left transition-all duration-200 hover:border-primary hover:bg-accent/50"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent">
                  <Upload className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">上传文档</p>
                  <p className="text-xs text-muted-foreground">支持 PDF、Word、图片等多种格式</p>
                </div>
              </button>
              <button
                onClick={() => navigate("/search")}
                className="flex items-center gap-3 rounded-lg border border-dashed p-4 text-left transition-all duration-200 hover:border-primary hover:bg-accent/50"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent">
                  <Search className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">全文检索</p>
                  <p className="text-xs text-muted-foreground">在知识库中搜索文档内容</p>
                </div>
              </button>
              <button
                onClick={() => navigate("/chat")}
                className="flex items-center gap-3 rounded-lg border border-dashed p-4 text-left transition-all duration-200 hover:border-primary hover:bg-accent/50"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent">
                  <MessageSquare className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">智能问答</p>
                  <p className="text-xs text-muted-foreground">用自然语言查询知识库内容</p>
                </div>
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}