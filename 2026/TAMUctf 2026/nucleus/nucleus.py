import pefile

def extract_flag_statically(filename):
    with open(filename, 'rb') as f:
        current_data = f.read()
        
    flag = ""
    layer = 1
    
    print("[*] 정적 분석(Static Analysis)을 시작합니다...\n")
    
    while True:
        try:
            pe = pefile.PE(data=current_data)
            resource_data = None
            
            if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
                for rsrc in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                    if rsrc.id == pefile.RESOURCE_TYPE['RT_RCDATA']: 
                        for entry in rsrc.directory.entries:
                            if entry.id == 101: # 0x65
                                data_rva = entry.directory.entries[0].data.struct.OffsetToData
                                size = entry.directory.entries[0].data.struct.Size
                                resource_data = pe.get_memory_mapped_image()[data_rva:data_rva+size]
                                break
            
            if not resource_data:
                break
                
            key = resource_data[0] ^ 0x4D
            char_key = chr(key)
            flag += char_key
            print(f" - Layer {layer}: Found Key '{char_key}'")
            
            next_data = bytearray(len(resource_data))
            for i in range(len(resource_data)):
                next_data[i] = resource_data[i] ^ key
                
            current_data = bytes(next_data)
            layer += 1
            
        except Exception as e:
            print(f"오류 발생 또는 파싱 완료: {e}")
            break
            
    print("\n" + "="*40)
    print(f"[*] 추출 완료! 총 {layer-1} 겹의 껍질을 벗겼습니다.")
    
    print(f"[!] 복구된 플래그: {flag}")
    print(f"[!] 뒤집은 플래그: {flag[::-1]}")
    print("="*40)

extract_flag_statically('nucleus21.exe')
