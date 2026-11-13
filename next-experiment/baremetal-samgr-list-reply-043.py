"""Bounded decoder for audited status + Parcel::ReadString16Vector wire layout."""
import struct


def decode_list_reply(data):
    if len(data)>65536 or len(data)<8:
        raise ValueError('reply size is invalid')
    status,count=struct.unpack_from('<ii',data)
    if status:
        raise ValueError(f'SAMGR status={status}')
    if not 0<=count<=4096:
        raise ValueError('invalid string count')
    offset=8
    result=[]
    for _ in range(count):
        if len(data)-offset<4:
            raise ValueError('truncated string length')
        length=struct.unpack_from('<i',data,offset)[0]
        offset+=4
        if not 0<=length<=256:
            raise ValueError('string length is out of bounds')
        end=offset+2*(length+1)
        aligned=(end+3)&~3
        if aligned>len(data) or data[end-2:end]!=b'\0\0':
            raise ValueError('truncated or unterminated UTF16 string')
        try:
            result.append(data[offset:end-2].decode('utf-16-le',errors='strict'))
        except UnicodeDecodeError as error:
            raise ValueError('invalid UTF16 string') from error
        offset=aligned
    if offset!=len(data):
        raise ValueError('unexpected trailing reply data')
    return result
