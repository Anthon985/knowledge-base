import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText, CheckCircle, AlertCircle, X, Loader2 } from "lucide-react"
import { uploadDocument, formatFileSize } from "@/lib/api"

interface UploadItem {
  file: File
  status: "pending" | "uploading" | "success" | "error"
  progress: number
  error?: string
}

export function UploadPage() {
  const [items, setItems] = useState<UploadItem[]>([])
  const [isDragOver, setIsDragOver] = useState(false)

  const addFiles = useCallback((files: FileList | null) => {
    if (!files) return
    const newItems: UploadItem[] = Array.from(files).map((file) => ({
      file,
      status: "pending" as const,
      progress: 0,
    }))
    setItems((prev) => [...prev, ...newItems])
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      addFiles(e.dataTransfer.files)
    },
    [addFiles]
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false)
  }, [])

  const removeItem = useCallback((index: number) => {
    setItems((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const uploadAll = useCallback(async () => {
    const pendingIndexes = items
      .map((item, i) => (item.status === "pending" ? i : -1))
      .filter((i) => i >= 0)

    for (const idx of pendingIndexes) {
      setItems((prev) =>
        prev.map((item, i) => (i === idx ? { ...item, status: "uploading" as const, progress: 30 } : item))
      )
      try {
        await uploadDocument(items[idx].file)
        setItems((prev) =>
          prev.map((item, i) => (i === idx ? { ...item, status: "success" as const, progress: 100 } : item))
        )
      } catch (err) {
        setItems((prev) =>
          prev.map((item, i) =>
            i === idx
              ? { ...item, status: "error" as const, error: err instanceof Error ? err.message : "上传失败" }
              : item
          )
        )
      }
    }
  }, [items])

  const pendingCount = items.filter((i) => i.status === "pending").length
  const isUploading = items.some((i) => i.status === "uploading")

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">上传文档</h2>
        <p className="text-muted-foreground mt-1">将文档上传到知识库进行电子化处理</p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-all duration-300 ${
              isDragOver
                ? "border-primary bg-accent/50 animate-upload-pulse"
                : "border-border hover:border-primary/50 hover:bg-accent/30"
            }`}
          >
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent mb-4">
              <Upload className={`h-8 w-8 text-primary transition-transform duration-300 ${isDragOver ? "scale-110" : ""}`} />
            </div>
            <p className="text-base font-medium">拖拽文件到此处上传</p>
            <p className="mt-1 text-sm text-muted-foreground">支持 PDF、Word、Excel、PPT、图片、Markdown 等格式</p>
            <label className="mt-4">
              <input
                type="file"
                multiple
                className="hidden"
                onChange={(e) => addFiles(e.target.files)}
                accept=".pdf,.docx,.doc,.xlsx,.xls,.pptx,.ppt,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.webp,.md,.txt,.html,.htm,.csv"
              />
              <span className="inline-flex cursor-pointer items-center rounded-md border border-input bg-card px-4 py-2 text-sm font-medium transition-colors hover:bg-accent">
                浏览文件
              </span>
            </label>
          </div>
        </CardContent>
      </Card>

      {items.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">上传队列 ({items.length} 个文件)</CardTitle>
            <Button onClick={uploadAll} disabled={pendingCount === 0 || isUploading} size="sm">
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  上传中...
                </>
              ) : (
                `上传全部 (${pendingCount})`
              )}
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {items.map((item, idx) => (
                <div key={idx} className="flex items-center gap-3 rounded-lg border p-3">
                  <div className="shrink-0">
                    {item.status === "success" ? (
                      <CheckCircle className="h-5 w-5 text-success" />
                    ) : item.status === "error" ? (
                      <AlertCircle className="h-5 w-5 text-destructive" />
                    ) : item.status === "uploading" ? (
                      <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    ) : (
                      <FileText className="h-5 w-5 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(item.file.size)}
                      {item.error && <span className="text-destructive ml-2">{item.error}</span>}
                    </p>
                  </div>
                  {item.status === "uploading" && (
                    <div className="w-24 h-1.5 rounded-full bg-secondary overflow-hidden">
                      <div className="h-full gradient-primary rounded-full transition-all duration-500" style={{ width: `${item.progress}%` }} />
                    </div>
                  )}
                  {(item.status === "pending" || item.status === "error") && (
                    <button onClick={() => removeItem(idx)} className="shrink-0 text-muted-foreground hover:text-foreground">
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}