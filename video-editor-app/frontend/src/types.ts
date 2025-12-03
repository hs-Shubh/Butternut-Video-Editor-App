export type Position = { x: number; y: number }

export type Overlay = {
  id: string
  type: 'text' | 'image' | 'video'
  content: string
  position: Position
  scale: number
  rotation: number
  opacity: number
  start_time: number
  end_time: number
  z_index: number
  font_size?: number
  background_box?: boolean
}

export type Resolution = { width: number; height: number }

export type Metadata = {
  title: string
  overlays: Overlay[]
  output_format: 'mp4'
  resolution: Resolution
}
