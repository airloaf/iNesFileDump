''' This file reads an INes
'''

def readRom(romPath):
    """ Reads the given file and returns the byte dump of the file

    Arguments:
        romPath - the path to the rom
    """

    # Open the file in binary mode
    rom = open(romPath, 'rb')
    header = readHeader(rom)

    data = {}
    data['Header'] = header
    
    if(header['PRG_ROM'] > 0):
        data['PRG_ROM'] = readPrgRom(rom, header['PRG_ROM'])
    
    if(header['CHR_ROM'] > 0):
        data['CHR_ROM'] = readChrRom(rom, header['CHR_ROM'])

    rom.close()
    return data

def readPrgRom(romFile, prgSize):
    """ Reads the program rom from the file stream.
    """
    return romFile.read(prgSize)

def readChrRom(romFile, chrSize):
    """ Read the character rom
    """
    return romFile.read(chrSize * 0x2000)

def readHeader(romFile):
    """ Reads the header (first 16 bytes) of the given
    file stream.
    
    Arguments:
        romFile - A file stream to the rom file
    """

    # Reads the format, first four bytes
    # For an iNes 1.0 file, the four bytes
    # should be "NES" followed by 0x1A
    romFormat = romFile.read(4)

    # Byte order doesn't matter, but is required for int.from_bytes
    prgRomSize = int.from_bytes(bytes=romFile.read(1), byteorder="big", signed=False) * 0x4000
    chrRomSize = int.from_bytes(bytes=romFile.read(1), byteorder="big", signed=False)

    flag6 = int.from_bytes(bytes=romFile.read(1), byteorder="big", signed=False)
    mirroring = flag6 & 0x01
    persistentStorage = True if (flag6 & 0x02 == 2) else False
    trainer = True if (flag6 & 0x04 == 1) else False

    # The ignore mapping bit
    # If 1, we ignore the mapping
    # else we use the mirroring
    ignoreMirroring = flag6 & 0x08
    if ignoreMirroring == 1:
        mirroring = None

    # Get the mapper value from the top 4 bits of flag 6 and 7
    flag7 = int.from_bytes(bytes=romFile.read(1), byteorder="big", signed=False)
    mapper = (flag6 & 0xF0) >> 4
    mapper += (flag7 & 0xF0)
    
    prgRamSize = int.from_bytes(bytes=romFile.read(1), byteorder="big", signed=False)

    # Ignore all other 7 bytes 
    romFile.read(7)

    # Create a dictionary to store the header information 
    header = {}
    header["Format"] = romFormat
   
    header["PRG_ROM"] = prgRomSize
    header["CHR_ROM"] = chrRomSize
    header["PRG_RAM"] = prgRamSize
    
    header["Mirroring"] = mirroring
    header["Persistent"] = persistentStorage
    header["Trainer"] = trainer
    header["Mapper"] = mapper

    return header