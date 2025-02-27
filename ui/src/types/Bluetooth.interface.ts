export interface BluetoothDevice {
    powered: boolean;
    address: string | undefined;
    hostname: string | undefined;
    discoverable: boolean;
    devices: Device[];
}

export interface Device {
    name: string;
    alias: string;
    address: string;
    connected: boolean;
    media: boolean;
    ancs: boolean;
}