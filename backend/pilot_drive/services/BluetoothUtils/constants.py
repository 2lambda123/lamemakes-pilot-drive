from enum import StrEnum

'''
Constants used for Bluetooth functionality.

Most are hardcoded strings created in hopes to mitigate string typo errors (and enums are cool!)
'''


class IFaceTypes(StrEnum):
    '''
    Enum used to properly address/pull different interfaces

    Bluez media API docs: https://github.com/bluez/bluez/blob/master/doc/media-api.txt
    '''

    BLUEZ = "org.bluez"  # Overarching bluez DBus interface
    MEDIA_PLAYER_1 = "org.bluez.MediaPlayer1"  # Responsible for most metadata on the tracks, provides title, artist, album, duration, postion, etc.
    MEDIA_TRANSPORT_1 = (
        "org.bluez.MediaTransport1"  # Provides track state such as idle or active
    )
    MEDIA_FOLDER_1 = "org.bluez.MediaFolder1"
    MEDIA_ITEM_1 = "org.bluez.MediaItem1"  # Also can be a metadata provider for tracks, not used currently.
    DEVICE_1 = "org.bluez.Device1"  # Used to pull device info
    ADAPTER_1 = "org.bluez.Adapter1"  # Used to determine things like if bluetooth is enabled on the host


class MediaPlayerAttributes(StrEnum):
    '''
    Enum used for the attributes of the MediaPlayer iface

    Bluez media API docs: https://github.com/bluez/bluez/blob/master/doc/media-api.txt
    '''

    NAME = "Name"
    SHUFFLE = "Shuffle"
    REPEAT = "Repeat"
    SCAN = "Scan"
    STATUS = "Status"
    POSITION = "Position"
    TRACK = "Track"
    TYPE = "Type"
    SUBTYPE = "Subtype"
    BROWSABLE = "Browsable"
    SEARCHABLE = "Searchable"


class MediaItemAttributes(StrEnum):
    '''
    Enum used for the attributes of the MediaItem iface

    Bluez transport API docs: https://github.com/bluez/bluez/blob/master/doc/media-api.txt
    '''

    METADATA = "Metadata"
    VOLUME = "Volume"


class MediaTransportAttributes(StrEnum):
    '''
    Enum used for the attributes of the MediaTransport iface

    Bluez transport API docs: https://github.com/bluez/bluez/blob/master/doc/media-api.txt
    '''

    STATE = "State"


class AdapterAttributes(StrEnum):
    '''
     Enum used for the attributes of the Adapter iface

    Bluez adapter API docs: https://github.com/bluez/bluez/blob/master/doc/adapter-api.txt
    '''

    CLASS = "Class"
    POWER_STATE = "PowerState"
    POWERED = "Powered"


class PowerStates(StrEnum):
    '''
    Enum used for the power states of the Adapter iface

    PowerStates docs: https://github.com/bluez/bluez/blob/master/doc/adapter-api.txt#L280-#L285
    '''

    ON = "on"
    OFF = "off"
    OFF_ENABLING = "off-enabling"
    ON_DISABLING = "on-disabling"
    OFF_BLOCKED = "off-blocked"


class TrackStatus(StrEnum):
    '''
    Enum used for the track status states

    Status state docs: https://github.com/bluez/bluez/blob/master/doc/media-api.txt#L271-#L275
    '''

    PLAYING = "playing"
    STOPPED = "stopped"
    PAUSED = "paused"
    FORWARD_SEEK = "forward-seek"
    REVERSE_SEEK = "reverse-seek"
    ERROR = "error"


class TrackControl(StrEnum):
    '''
    Enum used to handle values passed from the frontend regarding track control
    '''

    PAUSE = "pause"
    PLAY = "play"
    NEXT = "next"
    PREV = "prev"


class TrackAttributes(StrEnum):
    '''
    Enum used for the track attributes.

    Bluez docs: https://github.com/bluez/bluez/blob/master/doc/media-api.txt#L288-#L320
    '''

    TITLE = "Title"  # Responsible for most metadata on the tracks, provides title, artist, album, duration, postion, etc.
    ALBUM = "Album"  # Provides track state such as idle or active
    ARTIST = "Artist"
    DURATION = "Duration"
    GENRE = "Genre"
    TRACK_NUMBER = "TrackNumber"
    NUMBER_OF_TRACKS = "NumberOfTracks"


class Device(StrEnum):
    '''
    Enum used for the attributes of the Device iface

    Bluez device API docs: https://github.com/bluez/bluez/blob/master/doc/device-api.txt
    '''

    CONNECTED = "Connected"
    ADDRESS = "Address"
    NAME = "Name"
    ALIAS = "Alias"
    TRUSTED = "Trusted"
    RSSI = "RSSI"
    PAIRED = "Paired"
    UUIDS = "UUIDs"
    ICON = "Icon"


class MediaSources(StrEnum):
    '''
    Enum used for the media source passed to the frontend
    '''

    BLUETOOTH = "bluetooth"
    RADIO = "radio"
    FILES = "files"