// place files you want to import through the `$lib` alias in this folder.


export interface user {
    username: string;
    displayname: string;
    permissions: Number;
    creation_date: string;
}

export interface message { 
    message: string;
    author: user | string;
    timestamp: string;
    type: Number;
    ephemeral: boolean;
}