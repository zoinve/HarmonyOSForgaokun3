/* Included after wait_flip, within the composer's state namespace. */
static CursorSnapshot032 cursor_snapshot_032()
{
    if(!state.cursor_wire)state.cursor_wire=cursor_map_032(false);
    CursorSnapshot032 c{0,-1,-1,false};
    (void)cursor_read_032(state.cursor_wire,c);return c;
}
static bool same_cursor_032(const CursorSnapshot032 &a,const CursorSnapshot032 &b)
{
    return a.screen==b.screen && a.x==b.x && a.y==b.y && a.visible==b.visible;
}
static bool paint_cursor_032(Scanout &output)
{
    return cursor_frame_032(static_cast<unsigned char *>(output.map),output.size,output.pitch,
        state.drm.mode.hdisplay,state.drm.mode.vdisplay,state.cursor_background,cursor_snapshot_032());
}
static void cursor_tick_032()
{
    std::unique_lock<std::mutex> lock(state.mutex);
    CursorSnapshot032 last{0,-1,-1,false};unsigned reports=0;
    while(!state.stop){
        state.wake.wait_for(lock,std::chrono::milliseconds(8),[]{return state.stop;});
        if(state.stop)break;
        if(state.front<0 || state.cursor_background.empty())continue;
        auto current=cursor_snapshot_032();
        if(same_cursor_032(current,last))continue;
        if(wait_flip())continue; // A pending scanout is never recycled.
        int slot=state.front==0?1:0;auto &output=state.buffers[slot];
        dma_buf_sync sync={DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE};
        if(ioctl(output.dma_fd,DMA_BUF_IOCTL_SYNC,&sync))continue;
        bool painted=paint_cursor_032(output);
        sync.flags=DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE;
        if(ioctl(output.dma_fd,DMA_BUF_IOCTL_SYNC,&sync) || !painted)continue;
        state.pending_slot=slot;
        if(drmModePageFlip(state.drm.fd,state.drm.crtc,output.fb,DRM_MODE_PAGE_FLIP_EVENT,nullptr))continue;
        state.pending=true;
        if(wait_flip())continue;
        last=current;
        if(reports++<8)std::fprintf(stderr,"NATIVE_CURSOR032 scanout screen=%llu x=%d y=%d visible=%d\n",
            static_cast<unsigned long long>(last.screen),last.x,last.y,last.visible);
    }
}
