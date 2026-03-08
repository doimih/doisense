import { describe, it, expect } from '@jest/globals'
import { mount } from '@vue/test-utils'
import ChatBubble from '../../components/ChatBubble.vue'

describe('ChatBubble', () => {
  it('renders message', () => {
    const wrapper = mount(ChatBubble, {
      props: { message: 'Hello', isUser: true },
    })
    expect(wrapper.text()).toContain('Hello')
  })

  it('applies user class when isUser is true', () => {
    const wrapper = mount(ChatBubble, {
      props: { message: 'Hi', isUser: true },
    })
    const span = wrapper.find('span')
    expect(span.classes()).toContain('bg-amber-600')
  })

  it('applies bot class when isUser is false', () => {
    const wrapper = mount(ChatBubble, {
      props: { message: 'Hi', isUser: false },
    })
    const span = wrapper.find('span')
    expect(span.classes()).toContain('bg-stone-200')
  })
})
