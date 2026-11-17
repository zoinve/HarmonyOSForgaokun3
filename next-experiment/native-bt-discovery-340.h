#ifndef NATIVE_BT_DISCOVERY_340_H
#define NATIVE_BT_DISCOVERY_340_H
/* Read-only H4 classification. Constants follow Linux include/net/bluetooth/hci.h. */
static int bt340_scan_opcode(unsigned opcode)
{return opcode==0x0401||opcode==0x200c||opcode==0x2042;}
static int bt340_le_reports(const unsigned char *p,size_t n)
{
    if(n<5||!p[4]||(p[3]!=2&&p[3]!=0x0d))return 0;
    size_t offset=5,base=p[3]==2?10:24,length_offset=p[3]==2?8:23;
    for(unsigned i=0;i<p[4];++i){
        if(n-offset<base)return 0;
        size_t bytes=base+p[offset+length_offset];
        if(bytes>n-offset)return 0;
        offset+=bytes;
    }
    return offset==n;
}
static int bt340_command(const unsigned char *p,size_t n)
{
    if(n<4||p[0]!=1||n!=(size_t)p[3]+4)return 0;
    unsigned opcode=p[1]|((unsigned)p[2]<<8);
    if(!bt340_scan_opcode(opcode))return 0;
    int enable=-1;
    if((opcode==0x200c||opcode==0x2042)&&n>=5)enable=p[4];
    dprintf(1,"BT340_SCAN_COMMAND opcode=%04x enable=%d command_not_completion=1\n",opcode,enable);
    return 1;
}
static int bt340_event(const unsigned char *p,size_t n)
{
    if(n<3||p[0]!=4||n!=(size_t)p[2]+3)return 0;
    unsigned opcode=0,status=0;
    if(p[1]==0x0e&&n>=7){opcode=p[4]|((unsigned)p[5]<<8);status=p[6];}
    if(p[1]==0x0f&&n==7){opcode=p[5]|((unsigned)p[6]<<8);status=p[3];}
    if(bt340_scan_opcode(opcode)){
        dprintf(1,"BT340_SCAN_STATUS opcode=%04x status=%u event=%02x\n",opcode,status,p[1]);
        return 1;
    }
    if(p[1]==1&&n==4){
        dprintf(1,"BT340_INQUIRY_COMPLETE status=%u\n",p[3]);return 1;
    }
    int kind=0;
    if((p[1]==2||p[1]==0x22)&&n>=4&&p[3]>0&&n==4+(size_t)p[3]*14)kind=1;
    if(p[1]==0x2f&&n==258&&p[3]==1)kind=1;
    if(p[1]==0x3e&&bt340_le_reports(p,n))kind=2;
    if(kind){
        static unsigned long reports[3];
        unsigned long count=++reports[kind];
        if(count==1||count%64==0)
            dprintf(1,"BT340_REPORT_PACKETS kind=%d count=%lu device_count_not_inferred=1 addresses_exported=0\n",kind,count);
    }
    return kind?2:0;
}
#endif
