/* Every Tali sprite fades slowly between expressions. All 100 poses are shared out
   so each Tali on a page gets its own set of 8, different from the others. */
(function () {
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var BASE = '/email/tali/all/', EACH = 8, HOLD = 6000;
  var ALL = ["001_Idle", "002_Blink", "003_Listening", "004_Look_right", "005_Look_up", "006_Look_down", "007_Talking_open", "008_Talking_O", "009_Talking_mid", "010_Ready", "011_Happy", "012_Big_grin", "013_Giggle", "014_Content", "015_Delighted", "016_Wink", "017_Blowing_a_kiss", "018_Cheeky", "019_Proud", "020_Thankful", "021_Cheer", "022_Jump_for_joy", "023_Flex", "024_Clapping", "025_Star_eyes", "026_Party", "027_Victory", "028_Dance_left", "029_Dance_right", "030_Hyped", "031_Shock", "032_Gasp", "033_Startled", "034_Mind_blown", "035_Oops", "036_Double_take", "037_Confused", "038_Wait_what", "039_Awe", "040_Eyes_popped", "041_Sad", "042_Crying", "043_Worried", "044_Nervous", "045_Ashamed", "046_Disappointed", "047_Tired", "048_Big_sigh", "049_Lonely", "050_Defeated", "051_Annoyed", "052_Angry", "053_Furious", "054_Grumpy", "055_Side_eye", "056_Smug", "057_Unimpressed", "058_Eye_roll", "059_Stubborn", "060_Huffing", "061_Thinking", "062_Hmm", "063_Bright_idea", "064_Calculating", "065_Question", "066_Pondering", "067_Remembering", "068_Doubtful", "069_Curious", "070_Eureka", "071_Explain_right", "072_Explain_left", "073_Explain_both", "074_Present_left", "075_Present_right", "076_Welcome", "077_Ta-da", "078_Emphasis", "079_Listing", "080_Big_gesture", "081_Dollar_eyes", "082_Approved", "083_On_the_phone", "084_Clipboard", "085_Gym_time", "086_Trophy", "087_Chat", "088_Client_love", "089_Stopwatch", "090_Progress_chart", "091_Asleep", "092_Yawn", "093_Bye", "094_Wave", "095_Wave_left", "096_Shy", "097_Peek", "098_Bow", "099_Shrug", "100_Hug"];
  // shuffle once per page (seeded by the path) so pages differ too
  var seed = 0, path = location.pathname;
  for (var c = 0; c < path.length; c++) seed = (seed * 31 + path.charCodeAt(c)) >>> 0;
  function rnd() { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }
  // Gym and trainer pages keep Tali upbeat; the grumpy faces stay on the consumer pages
  var GLOOMY = /Sad|Crying|Worried|Nervous|Ashamed|Disappointed|Tired|Big_sigh|Lonely|Defeated|Annoyed|Angry|Furious|Grumpy|Side_eye|Smug|Unimpressed|Eye_roll|Stubborn|Huffing|Shock|Gasp|Startled|Oops|Doubtful|Asleep|Yawn|Confused|Wait_what/;
  var business = /^\/(totality|for-pts|for-gyms|features|pricing|compare|online-training)(\.html)?$/.test(location.pathname);
  var pool = business ? ALL.filter(function (n) { return !GLOOMY.test(n); }) : ALL.slice();
  for (var i = pool.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)); var t = pool[i]; pool[i] = pool[j]; pool[j] = t; }
  var k = 0;

  function setup(img) {
    if (img.dataset.taliSwap) return;
    img.dataset.taliSwap = '1';
    var pic = img.parentNode && img.parentNode.tagName === 'PICTURE' ? img.parentNode : null;
    if (pic) Array.prototype.slice.call(pic.querySelectorAll('source')).forEach(function (s) { s.remove(); });
    // keep the sprite's current box so a narrower pose never changes the layout
    var r = img.getBoundingClientRect();
    if (r.height > 0) { img.style.height = r.height + 'px'; img.style.width = r.width + 'px'; }
    img.style.objectFit = 'contain'; img.style.objectPosition = '50% 100%';
    img.classList.add('tali-swap');
    var set = [], start = (k++ * EACH) % pool.length;
    for (var s = 0; s < EACH; s++) set.push(pool[(start + s) % pool.length]);
    set.forEach(function (p) { var im = new Image(); im.src = BASE + p + '.png'; });
    var cur = -1;
    function next() {
      cur = (cur + 1) % set.length;
      img.src = BASE + set[cur] + '.png';
    }
    setTimeout(function () { next(); setInterval(next, HOLD); }, 1200 + (k % 6) * 1000);
  }

  function scan() {
    var els = document.querySelectorAll('img.spr, picture.tali img, .tali-live img');
    Array.prototype.forEach.call(els, function (img) {
      if (img.dataset.taliSwap || img.dataset.taliWait) return;
      if (img.complete && img.naturalWidth) setup(img);
      else { img.dataset.taliWait = '1'; img.addEventListener('load', function () { setup(img); }, { once: true }); }
    });
  }
  function boot() {
    scan();
    if ('MutationObserver' in window) new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
