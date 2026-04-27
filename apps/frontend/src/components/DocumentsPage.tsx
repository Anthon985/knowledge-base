import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Trash2, RefreshCw, AlertCircle } from "lucide-react"
import {
  listDocuments,
  deleteDocument,
  type Document,
  formatFileSize,
  formatDate,
  getStatusLabel,
  getStatusColor,
} from "@/lib/api"

export function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  const loadDocs = async () => {
    setIsLoading(true)
    try {
      const res = await listDocuments(0, 100)
      setDocs(res.documents)
      setTotal(res.total)
    } catch {
      setDocs([])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadDocs()
  }, [])

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id)
      setDocs((prev) => prev.filter((d) => d.id !== id))
      setTotal((prev) => prev - 1)
    } catch {
      // ignore
    }
    setDeleteConfirm(null)
  }

  const fileTypeIcon = (contentType: string) => {
    if (contentType.includes("pdf")) return "PDF"
    if (contentType.includes("word") || contentType.includes("document")) return "DOC"
    if (contentType.includes("sheet") || contentType.includes("excel")) return "XLS"
    if (contentType.includes("presentation") || contentType.includes("powerpoint")) return "PPT"
    if (contentType.includes("image")) return "IMG"
    return "TXT"
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">文档管理</h2>
          <p className="text-muted-foreground mt-1">管理知识库中的所有文档 ({total} 个)</p>
        </div>
        <Button onClick={loadDocs} variant="outline" size="sm">
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          刷新
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-lg border bg-card animate-pulse-soft" />
          ))}
        </div>
      ) : docs.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <FileText className="mx-auto h-12 w-12 text-muted-foreground/30 mb-4" />
            <p className="text-base font-medium text-muted-foreground">暂无文档</p>
            <p className="text-sm text-muted-foreground mt-1">上传文档后将在此处显示</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">文档列表</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {docs.map((doc) => (
                <div key={doc.id} className="flex items-center gap-4 rounded-lg border p-4 transition-colors hover:bg-accent/30">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent">
                    <span className="text-xs font-bold text-accent-foreground">{fileTypeIcon(doc.content_type)}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{doc.original_filename}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs text-muted-foreground">{formatFileSize(doc.file_size)}</span>
                      <span className="text-xs text-muted-foreground">{formatDate(doc.created_at)}</span>
                      {doc.chunk_count > 0 && (
                        <span className="text-xs text-muted-foreground">{doc.chunk_count} 个分块</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-medium ${getStatusColor(doc.status)}`}>
                      {getStatusLabel(doc.status)}
                    </span>
                    {doc.status === "failed" && doc.error_message && (
                      <span title={doc.error_message}>
                        <AlertCircle className="h-4 w-4 text-destructive" />
                      </span>
                    )}
                    {deleteConfirm === doc.id ? (
                      <div className="flex items-center gap-1">
                        <Button size="sm" variant="destructive" onClick={() => handleDelete(doc.id)} className="h-7 text-xs">
                          确认
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => setDeleteConfirm(null)} className="h-7 text-xs">
                          取消
                        </Button>
                      </div>
                    ) : (
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => setDeleteConfirm(doc.id)}
                        className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}