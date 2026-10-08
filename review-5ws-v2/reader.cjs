(function(){
function project(r){return {sessions:1,sessionAttendance:r.attendance,activityParticipations:r.activities.reduce((n,a)=>n+a.attendance,0),staffSessions:r.cadres.reduce((n,c)=>n+c.count,0),uniquePeople:null};}
const reader={project};if(typeof module!=='undefined')module.exports=reader;if(typeof window!=='undefined')window.SESSION_READER=reader;
})();

