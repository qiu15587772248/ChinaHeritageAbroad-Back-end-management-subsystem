import './waves.css'

const context = '@@wavesContext'

function handleClick(el, binding) {
  const { value } = binding
  const modifiers = binding.modifiers || {}
  
  function handle(e) {
    const customOpts = { center: modifiers.center }
    const opts = Object.assign({}, 
      { ele: el, type: 'hit', color: 'rgba(0, 0, 0, 0.15)' }, 
      customOpts
    )
    const target = opts.ele
    
    if (target) {
      target.style.position = 'relative'
      target.style.overflow = 'hidden'
      
      const rect = target.getBoundingClientRect()
      const ripple = target.querySelector('.waves-ripple')
      
      if (ripple) {
        ripple.remove()
      }
      
      const rippleEl = document.createElement('span')
      rippleEl.className = 'waves-ripple'
      rippleEl.style.height = rippleEl.style.width = Math.max(rect.width, rect.height) + 'px'
      
      target.appendChild(rippleEl)
      
      const top = e.pageY - rect.top - rippleEl.offsetHeight / 2 
      const left = e.pageX - rect.left - rippleEl.offsetWidth / 2
      
      rippleEl.style.top = `${opts.center ? '50%' : top + 'px'}`
      rippleEl.style.left = `${opts.center ? '50%' : left + 'px'}`
      rippleEl.style.transform = `${opts.center ? 'translate(-50%, -50%)' : ''}`
      rippleEl.style.opacity = '1'
      rippleEl.style.backgroundColor = opts.color
      
      const animation = {
        translate: '',
        opacity: '0',
        transform: 'scale(2.5)'
      }
      
      rippleEl.dataset.hold = Date.now()
      rippleEl.dataset.scale = '1'
      
      setTimeout(() => {
        rippleEl.style.opacity = animation.opacity
        rippleEl.style.transform = animation.transform
        rippleEl.style.transition = 'all 750ms cubic-bezier(0.23, 1, 0.32, 1)'
        
        setTimeout(() => {
          rippleEl.remove()
        }, 750)
      }, 450)
    }
  }
  
  if (!el[context]) {
    el[context] = {
      removeHandle: handle
    }
  } else {
    el[context].removeHandle = handle
  }
  
  return handle
}

export default {
  bind(el, binding) {
    el.addEventListener('click', handleClick(el, binding), false)
  },
  update(el, binding) {
    el.removeEventListener('click', el[context].removeHandle, false)
    el.addEventListener('click', handleClick(el, binding), false)
  },
  unbind(el) {
    el.removeEventListener('click', el[context].removeHandle, false)
    el[context] = null
    delete el[context]
  }
} 