
import { Track } from "../types";

export class JamendoService {
  constructor(clientId: string) {
    // Deprecated
  }

  async getTracks(tag: string = 'epic'): Promise<Track[]> {
    return [];
  }
}
