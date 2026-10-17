from pathlib import Path
p=Path('D:/aramada/scripts/prepare-bajoran-utility-slots.py');s=p.read_text();s=s.replace("  t+='weapon3 = \"\"\\n'","  # Absent slots must be omitted; empty weapon names crash the engine.");p.write_text(s)
p=Path('D:/aramada/scripts/prepare-bajoran-federation-balance-repair.py');s=p.read_text();s=s.replace("t=put(t,'weapon'+str(i),'\"\"')","t=re.sub(r'(?mi)^weapon'+str(i)+r'[ \\t]*=[^\\r\\n]*(?:\\r?\\n)?','',t)");p.write_text(s)
