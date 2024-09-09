module.exports={
    DateTimeAsFilename:()=>{
        const date = new Date();
        const date_str= date.toLocaleDateString('tr-TR').split('.').reverse().join('_');
        const time_str =date.toLocaleTimeString('tr-TR').replace(/:/g,'_')
        return date_str+"_"+time_str;
    },

    CalculateDistance:(lat1, lon1, lat2, lon2)=> {
        const R =6371; // Radius of the earth in km
        const φ1 = lat1 * Math.PI/180; // φ, λ in radians
        const φ2 = lat2 * Math.PI/180;
        const Δφ = (lat2-lat1) * Math.PI/180;
        const Δλ = (lon2-lon1) * Math.PI/180;

        const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ/2) * Math.sin(Δλ/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

        const d = R * c; // in metres
        return d
    }

}





