import {Pipe} from '@angular/core';

@Pipe({
    name: 'mapToIterable',
    pure: false
})
export class MapToIterable {
    transform(map: {}, args: any[] = null): any {
        console.log(map)
        if (!map)
            return null;
        return Object.keys(map)
            .map((key) => ({ 'key': key, 'value': map[key] }));
    }
}